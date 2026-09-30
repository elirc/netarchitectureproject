"""Compile selected real capacity and reason rules in an owned SDK-only lab."""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import temporal_lab as common

RULES = [
    "MeetingAttendeesLimitCannotBeNegativeRule", "MeetingGuestsLimitCannotBeNegativeRule",
    "MeetingAttendeesLimitMustBeGreaterThanGuestsLimitRule", "MeetingGuestsNumberIsAboveLimitRule",
    "MeetingAttendeesNumberIsAboveLimitRule", "AttendeesLimitCannotBeChangedToSmallerThanActiveAttendeesRule",
    "MeetingMustHaveAtLeastOneHostRule", "ReasonOfRemovingAttendeeFromMeetingMustBeProvidedRule",
]
FILES = ["BuildingBlocks/Domain/" + name + ".cs" for name in
         ["ValueObject", "IgnoreMemberAttribute", "IBusinessRule", "BusinessRuleValidationException"]]
FILES += ["Modules/Meetings/Domain/Meetings/MeetingLimits.cs"]
FILES += ["Modules/Meetings/Domain/Meetings/Rules/" + name + ".cs" for name in RULES]
PROGRAM = r'''
using CompanyName.MyMeetings.BuildingBlocks.Domain;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings.Rules;
int passed = 0;
string current = "initialization";
void Check(string label, bool condition) { current = label; if (!condition) throw new Exception("Prediction disagreed"); passed++; }
void Reject<T>(string label, Action action) where T : IBusinessRule {
    current = label;
    try { action(); }
    catch (BusinessRuleValidationException error) { if (error.BrokenRule is not T) throw; passed++; return; }
    throw new Exception("Expected rule rejection");
}
try {
    foreach (var row in new (int? total, int guests)[] { (null,0), (null,3), (8,3), (1,0) }) {
        current = $"valid limits {row}";
        var limits = MeetingLimits.Create(row.total, row.guests);
        Check(current, limits.AttendeesLimit == row.total && limits.GuestsLimit == row.guests);
    }
    Reject<MeetingAttendeesLimitCannotBeNegativeRule>("negative total", () => MeetingLimits.Create(-1,0));
    Reject<MeetingGuestsLimitCannotBeNegativeRule>("negative guest limit", () => MeetingLimits.Create(null,-1));
    Reject<MeetingAttendeesLimitMustBeGreaterThanGuestsLimitRule>("equal configured limits", () => MeetingLimits.Create(3,3));
    foreach (var row in new (string name,int limit,int guests,bool broken)[] {
        ("guest below",3,2,false), ("guest equal",3,3,false), ("guest above",3,4,true),
        ("zero disables guest ceiling",0,4,false), ("negative request characterization",3,-1,false) })
        Check(row.name, new MeetingGuestsNumberIsAboveLimitRule(row.limit,row.guests).IsBroken() == row.broken);
    foreach (var row in new (string name,int? limit,int active,int guests,bool broken)[] {
        ("capacity below",8,6,0,false), ("capacity equal",8,6,1,false), ("capacity above",8,6,2,true),
        ("null total ceiling",null,20,3,false), ("member place included",5,5,0,true),
        ("creator plus party",5,1,3,false) })
        Check(row.name, new MeetingAttendeesNumberIsAboveLimitRule(row.limit,row.active,row.guests).IsBroken() == row.broken);
    foreach (var row in new (string name,int? limit,int active,bool broken)[] {
        ("change below occupancy",5,6,true), ("change equal occupancy",6,6,false),
        ("change above occupancy",7,6,false), ("change null ceiling",null,6,false) })
        Check(row.name, new AttendeesLimitCannotBeChangedToSmallerThanActiveAttendeesRule(MeetingLimits.Create(row.limit,0),row.active).IsBroken() == row.broken);
    foreach (var row in new (int hosts,bool broken)[] { (0,true), (1,false), (2,false) })
        Check($"host count {row.hosts}", new MeetingMustHaveAtLeastOneHostRule(row.hosts).IsBroken() == row.broken);
    foreach (var row in new (string name,string reason,bool broken)[] {
        ("null reason",null,true), ("empty reason","",true), ("whitespace reason characterization","   ",false),
        ("provided reason","schedule conflict",false) })
        Check(row.name, new ReasonOfRemovingAttendeeFromMeetingMustBeProvidedRule(row.reason).IsBroken() == row.broken);
    Console.WriteLine($"PASS {passed} real rule cases; aggregate ordering, persistence, and HTTP not executed");
    return 0;
} catch (Exception error) {
    Console.Error.WriteLine($"FAIL {current}: {error.GetType().Name}: {error.Message}");
    return 1;
}
'''

def hashes():
    return {name: hashlib.sha256((common.SOURCE / name).read_bytes()).hexdigest() for name in FILES}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["baseline", "broken-capacity-equality", "broken-guest-zero", "broken-reason-whitespace"], default="baseline")
    args = parser.parse_args()
    before = hashes()
    try:
        with tempfile.TemporaryDirectory(prefix="meeting-capacity-course-") as folder:
            work = Path(folder).resolve()
            if work.parent != Path(tempfile.gettempdir()).resolve() or not work.name.startswith("meeting-capacity-course-"):
                raise RuntimeError("Unexpected owned temporary directory")
            for name in FILES: shutil.copyfile(common.SOURCE / name, work / Path(name).name)
            mutations = {
                "broken-capacity-equality": ("MeetingAttendeesNumberIsAboveLimitRule.cs", "this._attendeesLimit.Value < _allActiveAttendeesWithGuestsNumber", "this._attendeesLimit.Value <= _allActiveAttendeesWithGuestsNumber"),
                "broken-guest-zero": ("MeetingGuestsNumberIsAboveLimitRule.cs", "this._guestsLimit > 0 && this._guestsLimit < _guestsNumber", "this._guestsLimit >= 0 && this._guestsLimit < _guestsNumber"),
                "broken-reason-whitespace": ("ReasonOfRemovingAttendeeFromMeetingMustBeProvidedRule.cs", "string.IsNullOrEmpty(_reason)", "string.IsNullOrWhiteSpace(_reason)"),
            }
            if args.mode in mutations:
                name, old, new = mutations[args.mode]
                common.replace_once(work / name, old, new)
            (work / "Program.cs").write_text(PROGRAM, encoding="utf-8")
            (work / "CapacityLab.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup></Project>', encoding="utf-8")
            (work / "NuGet.Config").write_text('<configuration><packageSources><clear /></packageSources></configuration>', encoding="utf-8")
            restored = common.run(["dotnet", "restore", "CapacityLab.csproj", "--configfile", "NuGet.Config", "--verbosity", "quiet"], work)
            if restored.returncode: raise RuntimeError("SDK restore failed; no semantic result")
            built = common.run(["dotnet", "build", "CapacityLab.csproj", "--no-restore", "--configuration", "Release", "--verbosity", "quiet"], work)
            if built.returncode: raise RuntimeError("Compilation failed; no semantic result")
            result = common.run(["dotnet", str(work / "bin/Release/net10.0/CapacityLab.dll")], work)
            print("Mode:", args.mode, "semantic exit:", result.returncode)
            return result.returncode
    finally:
        if hashes() != before: raise RuntimeError("Original rule source changed during lab")
        print("Original hashes unchanged:", len(FILES), "source files")

if __name__ == "__main__":
    sys.exit(main())

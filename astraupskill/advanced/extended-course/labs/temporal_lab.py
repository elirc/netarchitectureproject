"""Run copied real temporal domain sources in an owned SDK-only directory."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "modular-monolith-with-ddd" / "src"
FILES = [
    "BuildingBlocks/Domain/ValueObject.cs",
    "BuildingBlocks/Domain/IgnoreMemberAttribute.cs",
    "BuildingBlocks/Domain/IBusinessRule.cs",
    "BuildingBlocks/Domain/BusinessRuleValidationException.cs",
    "Modules/Meetings/Domain/SharedKernel/SystemClock.cs",
    "Modules/Meetings/Domain/Meetings/MeetingTerm.cs",
    "Modules/Meetings/Domain/Meetings/Term.cs",
    "Modules/Meetings/Domain/Meetings/Rules/MeetingTermMustEndAfterStartRule.cs",
]
PROGRAM = r'''
using CompanyName.MyMeetings.BuildingBlocks.Domain;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings.Rules;
using CompanyName.MyMeetings.Modules.Meetings.Domain.SharedKernel;

static MeetingTerm MapTerm(DateTime startDate, DateTime endDate) => MeetingTerm.CreateNewBetweenDates(startDate, endDate);
int passed = 0;
string current = "initialization";
void Check(string label, bool condition) { current = label; if (!condition) throw new Exception("Prediction disagreed"); passed++; }
void Reject(string label, Action action) {
    current = label;
    try { action(); }
    catch (BusinessRuleValidationException error) {
        if (error.BrokenRule is not MeetingTermMustEndAfterStartRule) throw;
        passed++; return;
    }
    throw new Exception("Expected strict-order rejection");
}
try {
    var start = new DateTime(2026, 10, 1, 9, 0, 0, DateTimeKind.Utc);
    foreach (var ticks in new long[] { 1, TimeSpan.TicksPerHour * 2, TimeSpan.TicksPerHour * 3 }) {
        current = "positive interval " + ticks;
        var value = MeetingTerm.CreateNewBetweenDates(start, start.AddTicks(ticks));
        Check(current, value.StartDate == start && value.EndDate == start.AddTicks(ticks));
    }
    Reject("equal interval", () => MeetingTerm.CreateNewBetweenDates(start, start));
    Reject("reversed interval", () => MeetingTerm.CreateNewBetweenDates(start, start.AddTicks(-1)));
    current = "mapping preserves requested end";
    var mapped = MapTerm(start, start.AddHours(3));
    Check(current, mapped.StartDate == start && mapped.EndDate == start.AddHours(3));
    SystemClock.Set(start.AddTicks(-1)); Check("clock before start", !mapped.IsAfterStart());
    SystemClock.Set(start); Check("clock exactly at start", !mapped.IsAfterStart());
    SystemClock.Set(start.AddTicks(1)); Check("clock after start", mapped.IsAfterStart());
    var rsvp = Term.CreateNewBetweenDates(start, start.AddHours(1));
    Check("RSVP includes start", rsvp.IsInTerm(start));
    Check("RSVP includes end", rsvp.IsInTerm(start.AddHours(1)));
    Check("RSVP includes interior", rsvp.IsInTerm(start.AddMinutes(30)));
    Check("RSVP excludes before", !rsvp.IsInTerm(start.AddTicks(-1)));
    Check("RSVP excludes after", !rsvp.IsInTerm(start.AddHours(1).AddTicks(1)));
    Check("NoTerm includes past", Term.NoTerm.IsInTerm(start.AddYears(-1)));
    Check("NoTerm includes future", Term.NoTerm.IsInTerm(start.AddYears(1)));
    var startOnly = Term.CreateNewBetweenDates(start, null);
    Check("start-only excludes before", !startOnly.IsInTerm(start.AddTicks(-1)));
    Check("start-only includes future", startOnly.IsInTerm(start.AddYears(1)));
    var endOnly = Term.CreateNewBetweenDates(null, start);
    Check("end-only includes past", endOnly.IsInTerm(start.AddYears(-1)));
    Check("end-only excludes after", !endOnly.IsInTerm(start.AddTicks(1)));
    Console.WriteLine($"PASS {passed} real temporal-domain cases; no handler, database, or HTTP integration claimed");
    return 0;
} catch (Exception error) {
    Console.Error.WriteLine($"FAIL {current}: {error.GetType().Name}: {error.Message}");
    return 1;
} finally { SystemClock.Reset(); }
'''


def hashes():
    return {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() for name in FILES}


def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8-sig")
    if text.count(old) != 1:
        raise RuntimeError("Source expression changed; review mutation before running")
    path.write_text(text.replace(old, new), encoding="utf-8")


def run(command, work):
    result = subprocess.run(command, cwd=work, capture_output=True, text=True, timeout=120)
    if result.stdout.strip(): print(result.stdout.strip())
    if result.stderr.strip(): print(result.stderr.strip(), file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["baseline", "broken-meeting-rule", "broken-mapping", "broken-clock", "broken-rsvp-end"], default="baseline")
    args = parser.parse_args()
    before = hashes()
    try:
        with tempfile.TemporaryDirectory(prefix="meeting-temporal-course-") as folder:
            work = Path(folder).resolve()
            if work.parent != Path(tempfile.gettempdir()).resolve() or not work.name.startswith("meeting-temporal-course-"):
                raise RuntimeError("Unexpected owned temporary directory")
            for name in FILES: shutil.copyfile(SOURCE / name, work / Path(name).name)
            if args.mode == "broken-meeting-rule": replace_once(work / "MeetingTermMustEndAfterStartRule.cs", "_endDate <= _startDate", "_endDate < _startDate")
            if args.mode == "broken-clock": replace_once(work / "MeetingTerm.cs", "SystemClock.Now > this.StartDate", "SystemClock.Now >= this.StartDate")
            if args.mode == "broken-rsvp-end": replace_once(work / "Term.cs", "this.EndDate.Value >= date", "this.EndDate.Value > date")
            program = PROGRAM
            if args.mode == "broken-mapping":
                original = "MeetingTerm.CreateNewBetweenDates(startDate, endDate)"
                if program.count(original) != 1: raise RuntimeError("Adapter signature changed")
                program = program.replace(original, "MeetingTerm.CreateNewBetweenDates(startDate, startDate)")
            (work / "Program.cs").write_text(program, encoding="utf-8")
            (work / "TemporalLab.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup></Project>', encoding="utf-8")
            (work / "NuGet.Config").write_text('<configuration><packageSources><clear /></packageSources></configuration>', encoding="utf-8")
            restored = run(["dotnet", "restore", "TemporalLab.csproj", "--configfile", "NuGet.Config", "--verbosity", "quiet"], work)
            if restored.returncode: raise RuntimeError("SDK asset restore failed; no semantic result")
            built = run(["dotnet", "build", "TemporalLab.csproj", "--no-restore", "--configuration", "Release", "--verbosity", "quiet"], work)
            if built.returncode: raise RuntimeError("Compilation failed; no semantic result")
            result = run(["dotnet", str(work / "bin/Release/net10.0/TemporalLab.dll")], work)
            print("Mode:", args.mode, "semantic exit:", result.returncode)
            return result.returncode
    finally:
        if hashes() != before: raise RuntimeError("Original domain source changed during lab")
        print("Original hashes unchanged:", len(FILES), "source files")


if __name__ == "__main__":
    sys.exit(main())

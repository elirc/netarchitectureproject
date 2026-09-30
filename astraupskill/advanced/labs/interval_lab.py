"""Compile copied real domain sources in a disposable SDK-only console lab.
No source repository files, dependencies, database, or Git state are modified.
"""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "modular-monolith-with-ddd" / "src"
FILES = [
    "BuildingBlocks/Domain/ValueObject.cs",
    "BuildingBlocks/Domain/IgnoreMemberAttribute.cs",
    "BuildingBlocks/Domain/IBusinessRule.cs",
    "BuildingBlocks/Domain/BusinessRuleValidationException.cs",
    "Modules/Meetings/Domain/SharedKernel/SystemClock.cs",
    "Modules/Meetings/Domain/Meetings/MeetingTerm.cs",
    "Modules/Meetings/Domain/Meetings/Rules/MeetingTermMustEndAfterStartRule.cs",
]
PROGRAM = r'''
using CompanyName.MyMeetings.BuildingBlocks.Domain;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings;
using CompanyName.MyMeetings.Modules.Meetings.Domain.Meetings.Rules;

static MeetingTerm MapRequestedTerm(DateTime startDate, DateTime endDate) =>
    MeetingTerm.CreateNewBetweenDates(startDate, endDate);

var start = new DateTime(2026, 10, 1, 9, 0, 0, DateTimeKind.Utc);
int passed = 0;
foreach (var ticks in new long[] { 1, TimeSpan.TicksPerHour * 2 }) {
    var end = start.AddTicks(ticks);
    var term = MeetingTerm.CreateNewBetweenDates(start, end);
    if (term.StartDate != start || term.EndDate != end) throw new Exception("Factory lost a boundary");
    passed++;
}
foreach (var ticks in new long[] { 0, -1 }) {
    try {
        MeetingTerm.CreateNewBetweenDates(start, start.AddTicks(ticks));
        throw new Exception("Invalid interval was accepted");
    } catch (BusinessRuleValidationException error) {
        if (error.BrokenRule is not MeetingTermMustEndAfterStartRule) throw;
        passed++;
    }
}
var mapped = MapRequestedTerm(start, start.AddHours(3));
if (mapped.StartDate != start || mapped.EndDate != start.AddHours(3)) throw new Exception("Mapping lost requested end");
Console.WriteLine($"PASS {passed + 1} real-domain interval/mapping cases; no persistence or handler integration claimed");
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["baseline", "broken-mapping", "broken-rule"], default="baseline")
    args = parser.parse_args()
    before = {rel: hashlib.sha256((SOURCE / rel).read_bytes()).hexdigest() for rel in FILES}
    # SDK-only target matches the .NET 10 SDK installed for this workshop.
    with tempfile.TemporaryDirectory(prefix="meeting-interval-lab-") as folder:
        work = Path(folder)
        for rel in FILES:
            destination = work / Path(rel).name
            shutil.copyfile(SOURCE / rel, destination)
        if args.mode == "broken-rule":
            rule = work / "MeetingTermMustEndAfterStartRule.cs"
            text = rule.read_text(encoding="utf-8-sig")
            original = "_endDate <= _startDate"
            if text.count(original) != 1: raise RuntimeError("Source rule changed; review the lab before mutation")
            rule.write_text(text.replace(original, "_endDate < _startDate"), encoding="utf-8")
        program = PROGRAM
        if args.mode == "broken-mapping":
            program = program.replace("CreateNewBetweenDates(startDate, endDate)", "CreateNewBetweenDates(startDate, startDate)")
        (work / "Program.cs").write_text(program, encoding="utf-8")
        (work / "IntervalLab.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup></Project>', encoding="utf-8")
        (work / "NuGet.Config").write_text('<configuration><packageSources><clear /></packageSources></configuration>', encoding="utf-8")
        subprocess.run(["dotnet", "restore", "IntervalLab.csproj", "--configfile", "NuGet.Config", "--verbosity", "quiet"], cwd=work, check=True, timeout=120)
        completed = subprocess.run(["dotnet", "run", "--project", "IntervalLab.csproj", "--no-restore", "--configuration", "Release"], cwd=work, timeout=120)
    after = {rel: hashlib.sha256((SOURCE / rel).read_bytes()).hexdigest() for rel in FILES}
    if after != before: raise RuntimeError("Original source changed while the disposable lab ran")
    print("Original domain source hashes unchanged. Mode:", args.mode)
    return completed.returncode

if __name__ == "__main__":
    sys.exit(main())

# Interview questions: modular-monolith-with-ddd (mini kit, added in B08)

**Gap filled:** the B01 READ-tier pack had no interview material (`training/README.md`: "No ... interview/"). These 8
questions turn the navigation pack into things you can say out loud. Answer each in about 2 minutes, citing a real file.
Sealed answers: `training/_answers/interview-questions.md`.

1. How does this repo stop the Meetings module from calling Payments' internals, and what happens when someone tries?
   (`src/Tests/ArchTests/Modules/ModuleTests.cs`)
2. Walk me through what happens between `POST api/meetings/meetings` and the database row. Where is the transaction boundary?
3. Modular monolith or microservices for a 6-developer team building this product? Defend your choice and say what would make
   you change it.
4. Why does a cross-module event go outbox → inbox → internal command? Wouldn't one hop be simpler?
5. "The outbox gives at-least-once delivery." What does the *consumer* have to do about that, and does this repo do it?
6. You're about to run two instances of this API against one database. What breaks first, and how would you find out before users do?
7. Payments is event-sourced and Meetings isn't. Name one benefit and one cost of that split, visible in the code.
8. Tell me about a bug you found by reading code rather than running it. (Use FD1, FD2 or FD3 from `learn/02-fire-drills.md`.)

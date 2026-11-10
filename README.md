### Hi, I'm Sagi

I'm a software developer and a third-year CS student at Afeka (GPA 90.9). Most of what I've
shipped so far is Android, in Kotlin and Jetpack Compose. This year I'm expanding into Compose
Multiplatform and full-stack web, and learning to build with AI coding tools the disciplined way:
getting the most out of them while understanding every line.

Before software, I spent 4+ years running IT infrastructure: as a sysadmin in the IDF, then as a
Microsoft Support Engineer at We Ankor, working with Microsoft 365, Azure, Intune and on-prem
Active Directory and Exchange.

**Open to student roles (development, DevOps, cloud), 2–3 days/week**, and planning to stay on after graduation.
Reach me at [sagi.einav@icloud.com](mailto:sagi.einav@icloud.com) or on
[LinkedIn](https://www.linkedin.com/in/sagi-einav).

---

### Featured projects

<a href="https://github.com/sagieinav/android-mono-task">
  <img src="https://repository-images.githubusercontent.com/1165552936/eb53298f-3bea-40f2-9317-5094bfead604" alt="MonoTask banner" width="100%">
</a>

**[MonoTask](https://github.com/sagieinav/android-mono-task)** is a gamified Android task manager
that shows you one task at a time. I built it solo, shipped 3 beta releases, and used
it as my daily task manager while building it, so bugs and UX gaps surfaced in real use.

- **Design system module.** 34 reusable Compose components across 8 screens, plus a hand-written
  swipe-gesture engine and charts drawn on Canvas.
- **Hybrid MVVM + MVI architecture.** Each screen exposes one immutable State, receives user
  actions as Events, and sends one-shot Effects (navigation, snackbars) on a separate channel, so
  they never replay on rotation. A shared base ViewModel enforces this contract, without the
  boilerplate of a full MVI framework.
- **Task-picking algorithm.** A logistic urgency curve is weighted against importance and
  penalized for each snooze, so the app decides what you should do next.
- **Real-time data.** Firestore is streamed to the UI as Flows. Streak and weekly-XP stats update
  in a single transaction.
- **87 unit tests** (JUnit 5, AssertK) cover XP, achievements, task selection and undo/restore.

`Kotlin` `Jetpack Compose` `Hilt` `Coroutines & Flow` `Firebase Auth` `Firestore` `DataStore`

<br>

<p>
  <a href="https://github.com/sagieinav/edu-vetrinator-game-android">
    <img src="https://github.com/user-attachments/assets/c0938090-77f7-474e-b32f-505f1eca87cd" alt="George The Vetrinator: main menu" height="240">
    <img src="https://github.com/user-attachments/assets/1e3a4f45-2820-4dd4-940c-0cdb2347c532" alt="George The Vetrinator: gameplay" height="240">
    <img src="https://github.com/user-attachments/assets/b5edb66e-ac11-47c2-9f8e-7df00271c3c0" alt="George The Vetrinator: gameplay in tilt-control mode" height="240">
  </a>
</p>

**[George The Vetrinator](https://github.com/sagieinav/edu-vetrinator-game-android)** is a
pixel-art arcade game parodying the Israeli sitcom *Haparlament*, and my first Android app.

- **Tilt controls that feel exact.** Sensor input is smoothed with a low-pass filter and a neutral
  zone, so one tilt moves exactly one lane.
- **Google Maps leaderboard** that pins each high score where it was set.

`Kotlin` `XML Views` `Coroutines` `Sensors` `Google Maps SDK`

---

### Currently

I'm in my third year, and three courses each end in a project I'm preparing to work on:

- **Final project** (two semesters, with a partner): an app in **Compose Multiplatform**, taking
  the Kotlin and Compose I used on Android to more than one platform.
- **Full-stack web app** (with a partner): **React** on the front end, **Node.js / Express** and
  **PostgreSQL** behind it, from first screen to deployment.
- **LLM-based development:** a project course on building software with AI coding tools the
  right way. The goal is the best results the tools can give, while I still understand and own
  every line, as opposed to vibe coding.

Also this semester: Software Engineering, Compilation, and Parallel & Distributed Computing.

### Skills

**Languages:** Kotlin · Java · Python · C · SQL · Bash<br>
**Android:** Jetpack Compose · XML Views · Coroutines & Flow · Hilt · Navigation · DataStore · Material 3<br>
**Architecture & data:** Clean Architecture · MVVM / MVI · Firebase Auth · Firestore · PostgreSQL<br>
**Tooling:** Git · Gradle · Docker · JUnit 5 · AssertK<br>
**IT & cloud:** PowerShell · Active Directory · Microsoft 365 · Azure · Intune · Exchange

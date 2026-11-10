## Hi, I'm Sagi

Software developer and third-year CS student at Afeka College of Engineering (GPA 90.9).

I build Android apps in Kotlin and Jetpack Compose, and I'm now expanding into Compose
Multiplatform, full-stack web and disciplined AI-assisted development.

Before that, 4+ years in IT infrastructure: sysadmin in the IDF, then Microsoft Support Engineer
at We Ankor (Microsoft 365, Azure, Intune, on-prem AD and Exchange).

**Open to student roles in development, DevOps or cloud, 2–3 days/week**, and planning to stay on
after graduation.

## Stack

**Languages:** <img src="https://img.shields.io/badge/Kotlin-30363D?style=flat&logo=kotlin&logoColor=7F52FF" alt="Kotlin"> <img src="https://img.shields.io/badge/Java-30363D?style=flat&logo=openjdk&logoColor=ED8B00" alt="Java"> <img src="https://img.shields.io/badge/Python-30363D?style=flat&logo=python&logoColor=4B8BBE" alt="Python"> <img src="https://img.shields.io/badge/C-30363D?style=flat&logo=c&logoColor=A8B9CC" alt="C"> <img src="https://img.shields.io/badge/Bash-30363D?style=flat&logo=gnubash&logoColor=4EAA25" alt="Bash"><br>
**Android:** <img src="https://img.shields.io/badge/Android-30363D?style=flat&logo=android&logoColor=3DDC84" alt="Android"> <img src="https://img.shields.io/badge/Jetpack%20Compose-30363D?style=flat&logo=jetpackcompose&logoColor=4285F4" alt="Jetpack Compose"> <img src="https://img.shields.io/badge/Coroutines%20%26%20Flow-30363D?style=flat" alt="Coroutines &amp; Flow"> <img src="https://img.shields.io/badge/Hilt-30363D?style=flat" alt="Hilt"> <img src="https://img.shields.io/badge/Material%203-30363D?style=flat&logo=materialdesign&logoColor=white" alt="Material 3"><br>
**Data & Tools:** <img src="https://img.shields.io/badge/Firebase-30363D?style=flat&logo=firebase&logoColor=FFCA28" alt="Firebase"> <img src="https://img.shields.io/badge/PostgreSQL-30363D?style=flat&logo=postgresql&logoColor=4169E1" alt="PostgreSQL"> <img src="https://img.shields.io/badge/Git-30363D?style=flat&logo=git&logoColor=F05032" alt="Git"> <img src="https://img.shields.io/badge/Gradle-30363D?style=flat&logo=gradle&logoColor=white" alt="Gradle"> <img src="https://img.shields.io/badge/Docker-30363D?style=flat&logo=docker&logoColor=2496ED" alt="Docker"> <img src="https://img.shields.io/badge/JUnit%205-30363D?style=flat&logo=junit5&logoColor=25A162" alt="JUnit 5"><br>
**IT & Cloud:** <img src="https://img.shields.io/badge/Azure-30363D?style=flat" alt="Azure"> <img src="https://img.shields.io/badge/Microsoft%20365-30363D?style=flat" alt="Microsoft 365"> <img src="https://img.shields.io/badge/PowerShell-30363D?style=flat" alt="PowerShell"> <img src="https://img.shields.io/badge/Active%20Directory-30363D?style=flat" alt="Active Directory"> <img src="https://img.shields.io/badge/Intune-30363D?style=flat" alt="Intune">

## Featured Projects

### [MonoTask](https://github.com/sagieinav/android-mono-task)

<a href="https://github.com/sagieinav/android-mono-task">
  <img src="https://repository-images.githubusercontent.com/1165552936/eb53298f-3bea-40f2-9317-5094bfead604" alt="MonoTask banner: one focused task card on a phone" width="100%">
</a>

A gamified Android task manager that shows one task at a time. Built solo, shipped in 3 beta
releases, and used daily as my own planner.

- **Design system:** 34 Compose components across 8 screens, a custom swipe-gesture engine, Canvas-drawn charts
- **Hybrid MVVM + MVI:** one immutable State per screen; one-shot Effects on a separate channel, so they never replay on rotation
- **Task-picking algorithm:** a logistic urgency curve, weighted against importance and penalized per snooze
- **Real-time data:** Firestore streamed as Flows; streak and XP stats update in a single transaction
- **87 unit tests** (JUnit 5, AssertK) on XP, achievements, task selection and undo/restore

### [George The Vetrinator](https://github.com/sagieinav/edu-vetrinator-game-android)

<a href="https://github.com/sagieinav/edu-vetrinator-game-android">
  <img src="https://github.com/user-attachments/assets/c0938090-77f7-474e-b32f-505f1eca87cd" alt="George The Vetrinator: main menu" height="240">
  <img src="https://github.com/user-attachments/assets/1e3a4f45-2820-4dd4-940c-0cdb2347c532" alt="George The Vetrinator: gameplay" height="240">
  <img src="https://github.com/user-attachments/assets/b5edb66e-ac11-47c2-9f8e-7df00271c3c0" alt="George The Vetrinator: gameplay in tilt-control mode" height="240">
</a>

My first Android app, a pixel-art arcade game parodying the sitcom *Haparlament*. Tilt input runs
through a low-pass filter and a neutral zone, so one tilt moves exactly one lane. High scores are
pinned on a Google Maps leaderboard.

## Currently

Expanding my skills, with 3 projects I'm planning to work on:

- **Degree's final project:** a Compose Multiplatform app, built with a partner over two semesters
- **Full-stack web:** React, Node.js / Express and PostgreSQL, from first screen to deployment
- **LLM-based development:** building with AI coding tools while understanding and owning every line, not vibe coding

## 1 Hi, I'm Sagi

Software developer and third-year CS student at Afeka (GPA 90.9).

I build Android apps in Kotlin and Jetpack Compose, with tested business logic and a design
system of my own. Before that, I spent 4+ years in IT infrastructure: sysadmin in the IDF, then
Microsoft Support Engineer at We Ankor (Microsoft 365, Azure, Intune, on-prem AD and Exchange).

**Open to student roles in development, DevOps or cloud, 2–3 days/week**, and planning to stay on
after graduation.

<a href="https://www.linkedin.com/in/sagi-einav/"><img src="assets/badges/linkedin.svg" alt="LinkedIn"></a>

## 2 Stack

**Languages:**&nbsp; <img src="assets/badges/kotlin.svg" alt="Kotlin"> <img src="assets/badges/java.svg" alt="Java"> <img src="assets/badges/python.svg" alt="Python"> <img src="assets/badges/c.svg" alt="C"> <img src="assets/badges/bash.svg" alt="Bash">

**Android:**&nbsp; <img src="assets/badges/android.svg" alt="Android"> <img src="assets/badges/compose.svg" alt="Jetpack Compose"> <img src="assets/badges/coroutines.svg" alt="Coroutines &amp; Flow"> <img src="assets/badges/hilt.svg" alt="Hilt"> <img src="assets/badges/material3.svg" alt="Material 3">

**Data & Tools:**&nbsp; <img src="assets/badges/firebase.svg" alt="Firebase"> <img src="assets/badges/postgresql.svg" alt="PostgreSQL"> <img src="assets/badges/git.svg" alt="Git"> <img src="assets/badges/gradle.svg" alt="Gradle"> <img src="assets/badges/docker.svg" alt="Docker"> <img src="assets/badges/junit5.svg" alt="JUnit 5">

**IT & Cloud:**&nbsp; <img src="assets/badges/azure.svg" alt="Azure"> <img src="assets/badges/m365.svg" alt="Microsoft 365"> <img src="assets/badges/powershell.svg" alt="PowerShell"> <img src="assets/badges/active-directory.svg" alt="Active Directory"> <img src="assets/badges/intune.svg" alt="Intune">


## 3 Featured Projects

<a href="https://github.com/sagieinav/android-mono-task"><img align="left" width="96" src="https://github.com/user-attachments/assets/1f8097ba-7108-4dbc-8c5c-4a6f92c4736e" alt="MonoTask app icon"></a>

### 3.1 [MonoTask](https://github.com/sagieinav/android-mono-task)

A gamified Android task manager that shows one task at a time. Built solo, shipped in
[3 beta releases](https://github.com/sagieinav/android-mono-task/releases), and used daily as my own planner.
<br clear="left">

<a href="https://github.com/sagieinav/android-mono-task"><img width="100%" src="https://github.com/user-attachments/assets/c8fa30fc-371c-48b1-93b4-0a9261094a2a" alt="Three MonoTask screens: a single focused task card, the all-done empty state, and the daily brief of overdue and due-today tasks"></a>

- **Design system:** 34 Compose components across 8 screens, a custom swipe-gesture engine, Canvas-drawn charts
- **Hybrid MVVM + MVI:** one immutable State per screen; one-shot Effects on a separate channel, so they never replay on rotation
- **Task-picking algorithm:** a logistic urgency curve, weighted against importance and penalized per snooze
- **Real-time data:** Firestore streamed as Flows; streak and XP stats update in a single transaction
- **87 unit tests** (JUnit 5, AssertK) on XP, achievements, task selection and undo/restore

<a href="https://github.com/sagieinav/edu-vetrinator-game-android"><img align="left" width="96" src="https://github.com/user-attachments/assets/f40e2544-97ac-4f3d-ba43-0545080cc45d" alt="George The Vetrinator icon: a pixel-art portrait of George"></a>

### 3.2 [George The Vetrinator](https://github.com/sagieinav/edu-vetrinator-game-android)

My first Android app, a pixel-art arcade game parodying the sitcom *Haparlament*. Tilt input runs
through a low-pass filter and a neutral zone, so one tilt moves exactly one lane. High scores are
pinned on a Google Maps leaderboard. <sub>*(Kotlin · Android sensors · Google Maps SDK)*</sub>
<br clear="left">

## 4 Now

- **Full-stack web:** React, Node.js / Express and PostgreSQL, from first screen to deployment
- **AI-assisted development:** building with AI coding tools while understanding and owning every line, not vibe coding

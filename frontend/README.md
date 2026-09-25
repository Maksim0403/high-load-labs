# LogiFlow — Frontend

![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=flat-square&logo=vue.js&logoColor=4FC08D)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat-square&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)
![Pinia](https://img.shields.io/badge/Pinia-FFE16B?style=flat-square&logo=vue.js&logoColor=black)

> LogiFlow is a logistics management platform that helps teams track shipments,
> manage warehouses, and automate delivery workflows.

## Application Preview

![LogiFlow Demo](./docs/animation.gif)

## Features

- Shipment tracking
- Warehouse management
- Delivery workflow automation

## Role-Based Interfaces & Responsive Design

LogiFlow provides tailored, responsive experiences depending on the user's role
and device:

![Manager Dashboard](./docs/manager-desktop.png)

![User Desktop](./docs/user-desktop.png)

![Driver Console](./docs/driver-mobile.png)

## Tech Stack

- Vue 3 + Vite
- TypeScript
- Vue Router
- Pinia
- ESLint + Prettier + oxlint

### State Management

The application uses **Pinia** as the Single Source of Truth:

- `authStore`: Manages the user session lifecycle, JWT tokens, and driver
  profile (including assigned vehicles).
- `routesStore`: Synchronizes logistics routes between the client and server
  using Optimistic UI updates.
- `notificationStore`: Global manager for toast notifications.

All stores are strictly typed using TypeScript (`Route`, `Order`, `Vehicle`).

## Getting Started

### Prerequisites

- Node.js >= 20

### Installation

```bash
git clone https://github.com/practice-team-lymhqo34/frontend.git
cd frontend
npm install
```

### Running

```bash
npm run dev
```

### Build for production

```bash
npm run build
npm run preview
```

### Running with Docker

The easiest way to launch the LogiFlow frontend along with its entire
ecosystem (Backend, S3 Storage) is using Docker Compose.

Run the following command in the root directory:

```bash
docker-compose up -d --build
```

The frontend application will be compiled, served via Nginx, and available at
`http://localhost:80` (or your specifically configured port).

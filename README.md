# Home Assistant TickTick Integration

![Static Badge](https://img.shields.io/badge/made%20with-fun-green?style=for-the-badge)‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎
![GitHub Repo stars](https://img.shields.io/github/stars/Hantick/ticktick-home-assistant?style=for-the-badge&color=%23AFB0CC)
![GitHub Release](https://img.shields.io/github/v/release/Hantick/ticktick-home-assistant?style=for-the-badge&color=%231CB00A)

Integration implements [TickTick Open API](https://developer.ticktick.com/docs#/openapi) with support for [To-do list](https://www.home-assistant.io/integrations/todo/) entities and exposes it as services in Home Assistant, allowing you to manage your tasks and projects programmatically 😎

## Buy me a coffee or beer 🍻
<a href="https://paypal.me/hantick" target="_blank" rel="noopener noreferrer">
    <img src="https://www.paypalobjects.com/marketing/web/logos/paypal-mark-color.svg" alt="PayPal" height="40"></a>

## Installation

1. Navigate to [TickTick Developer](https://developer.ticktick.com/manage) and click `New App`
2. Name your app and set `OAuth redirect URL` to `https://my.home-assistant.io/redirect/oauth` or your instance url i.e `http://homeassistant.local:8123`
3. Add this repository in HACS and download TickTick Integration via HACS
4. In Settings → Devices & services, use the dotted menu to create new application credentials (`/config/application_credentials`). Enter the OAuth client ID and secret from the TickTick app here.
5. Your TickTick Lists should now each turn up as a todo list in Home Assistant.

Your active TickTick Habits show up as a `Habits` todo list. A habit is checked off when it is done today. Checking or unchecking it in Home Assistant checks in or unchecks the habit in TickTick for today. Numeric habits show today's progress, i.e. `3/8 Cup`, in the description.

If you don’t want all of your lists to show up in the todo list app, you can disable selected lists in the entities list
(enter selection mode → Disable selected).

## Exposed Services

### Task Services

Get, Create, Update, Delete, Complete Task

### Project Services

Get (Create, Update, Delete are missing for now)

### Habit Services

Get Habits, Get Habit Check-ins, Check In Habit

## Left to be done:

- Create/Update Task Service: `items` - The list of subtasks
- Create/Update Task Service: `reminders` - Can create some better builder for reminders
- Create/Update Task Service: `repeatFlag` - Can create some better builder for reminders
- Get Project By ID Service
- Get Project By ID With Data Service
- Create Project
- Update Project
- Delete Project

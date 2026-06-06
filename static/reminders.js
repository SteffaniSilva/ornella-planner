// Ornella Planner browser reminders
// Reminders work while the website is open in the browser.

(function () {
    "use strict";

    const MAX_TIMEOUT = 2147483647; // maximum safe delay for setTimeout

    function canUseNotifications() {
        return "Notification" in window;
    }

    function askNotificationPermission() {
        if (!canUseNotifications()) {
            return Promise.resolve("unsupported");
        }

        if (Notification.permission === "granted") {
            return Promise.resolve("granted");
        }

        if (Notification.permission === "denied") {
            return Promise.resolve("denied");
        }

        return Notification.requestPermission();
    }

    function safeGetItem(key) {
        try {
            return localStorage.getItem(key);
        } catch (error) {
            return null;
        }
    }

    function safeSetItem(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (error) {
            // Ignore storage errors in private/incognito modes.
        }
    }

    function showReminder(task) {
        const message = `Reminder: ${task.title}`;

        if (canUseNotifications() && Notification.permission === "granted") {
            new Notification("Ornella Planner", {
                body: message,
                icon: "/static/images/planner.jpg"
            });
        } else {
            alert(message);
        }
    }

    function readReminderTasks() {
        const dataTag = document.getElementById("task-reminder-data");

        if (!dataTag) {
            return [];
        }

        try {
            return JSON.parse(dataTag.textContent || "[]");
        } catch (error) {
            console.error("Could not read reminder tasks", error);
            return [];
        }
    }

    function scheduleLongTimeout(callback, delay) {
        if (delay <= MAX_TIMEOUT) {
            window.setTimeout(callback, delay);
            return;
        }

        window.setTimeout(function () {
            scheduleLongTimeout(callback, delay - MAX_TIMEOUT);
        }, MAX_TIMEOUT);
    }

    function scheduleReminders() {
        const tasks = readReminderTasks();

        tasks.forEach(function (task) {
            if (!task.due_date || !task.due_time || task.status === "Completed") {
                return;
            }

            const dueAt = new Date(`${task.due_date}T${task.due_time}`);
            const delay = dueAt.getTime() - Date.now();
            const reminderKey = `ornella-reminder-shown-${task.id}-${task.due_date}-${task.due_time}`;

            if (Number.isNaN(dueAt.getTime()) || delay <= 0 || safeGetItem(reminderKey)) {
                return;
            }

            scheduleLongTimeout(function () {
                safeSetItem(reminderKey, "yes");
                showReminder(task);
            }, delay);
        });
    }

    function attachPermissionHandlers() {
        document.querySelectorAll(".js-enable-reminders").forEach(function (element) {
            element.addEventListener("click", function (event) {
                const targetUrl = element.getAttribute("href");

                if (targetUrl) {
                    event.preventDefault();
                }

                askNotificationPermission().finally(function () {
                    if (targetUrl) {
                        window.location.href = targetUrl;
                    }
                });
            });
        });

        document.querySelectorAll(".js-reminder-form").forEach(function (form) {
            form.addEventListener("submit", function (event) {
                const dueDate = form.querySelector('input[name="due_date"]');
                const dueTime = form.querySelector('input[name="due_time"]');

                if (!dueDate || !dueTime || !dueDate.value || !dueTime.value) {
                    return;
                }

                if (!canUseNotifications() || Notification.permission !== "default") {
                    return;
                }

                event.preventDefault();
                askNotificationPermission().finally(function () {
                    form.submit();
                });
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        attachPermissionHandlers();
        scheduleReminders();
    });
})();

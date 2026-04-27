package com.metaengine.demo.notification.enums;

/** Channel enum for the notification domain. */
public enum Channel {
    EMAIL(0),
    SMS(1),
    PUSH(2),
    WEBHOOK(3);

    private final int value;

    Channel(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}

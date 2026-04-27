package com.metaengine.demo.notification.enums;

// Channel enum.

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

    public static Channel fromValue(int value) {
        for (Channel item : Channel.values()) {
            if (item.value == value) {
                return item;
            }
        }
        throw new IllegalArgumentException("Unknown value: " + value);
    }
}

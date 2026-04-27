package com.metaengine.demo.analytics.enums;

// EventType enum.

public enum EventType {
    CLICK(0),
    VIEW(1),
    PURCHASE(2),
    SIGNUP(3);

    private final int value;

    EventType(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public static EventType fromValue(int value) {
        for (EventType item : EventType.values()) {
            if (item.value == value) {
                return item;
            }
        }
        throw new IllegalArgumentException("Unknown value: " + value);
    }
}

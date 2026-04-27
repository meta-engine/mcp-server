package com.metaengine.demo.analytics.enums;

/** EventType enum for the analytics domain. */
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
}

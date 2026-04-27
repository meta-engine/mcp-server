package com.metaengine.demo.analytics.enums;

/** Type classification for an analytics Event. */
public enum EventType {
    Click(0),
    View(1),
    Purchase(2),
    Signup(3);

    private final int value;

    EventType(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}

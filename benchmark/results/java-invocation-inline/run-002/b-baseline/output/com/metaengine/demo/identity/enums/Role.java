package com.metaengine.demo.identity.enums;

/** Role enum for the identity domain. */
public enum Role {
    ADMIN(0),
    USER(1),
    SERVICE(2);

    private final int value;

    Role(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}

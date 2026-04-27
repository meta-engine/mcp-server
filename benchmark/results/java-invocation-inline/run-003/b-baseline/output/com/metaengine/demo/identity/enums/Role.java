package com.metaengine.demo.identity.enums;

/** Role enum for the identity domain. */
public enum Role {
    Admin(0), User(1), Service(2);

    private final int value;

    Role(int value) { this.value = value; }

    public int getValue() { return value; }
}

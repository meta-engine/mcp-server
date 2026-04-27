package com.metaengine.demo.identity.enums;

/** Roles that can be assigned to a user. */
public enum Role {
    Admin(0),
    User(1),
    Service(2);

    private final int value;

    Role(int value) { this.value = value; }

    public int getValue() { return value; }
}

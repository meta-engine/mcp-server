package com.metaengine.demo.notification.enums;

/** Channel enum in the notification domain. */
public enum Channel {
    Email(0),
    Sms(1),
    Push(2),
    Webhook(3);

    private final int value;

    Channel(int value) { this.value = value; }

    public int getValue() { return value; }
}

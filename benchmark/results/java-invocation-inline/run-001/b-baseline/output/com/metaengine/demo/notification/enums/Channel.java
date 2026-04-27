package com.metaengine.demo.notification.enums;

/** Supported notification delivery channels. */
public enum Channel {
    Email(0),
    Sms(1),
    Push(2),
    Webhook(3);

    private final int value;

    Channel(int value) { this.value = value; }

    public int getValue() { return value; }
}

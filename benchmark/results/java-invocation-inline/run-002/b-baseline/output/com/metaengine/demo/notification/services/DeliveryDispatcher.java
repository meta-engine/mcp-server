package com.metaengine.demo.notification.services;

import java.util.List;

import com.metaengine.demo.notification.aggregates.Notification;

/** DeliveryDispatcher for the notification domain. */
public class DeliveryDispatcher {

    /** Create a new Notification from partial input. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Notification by id. Returns null if not found. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Notifications up to the given limit. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete the Notification with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

package com.metaengine.demo.notification.services;

import com.metaengine.demo.notification.aggregates.Notification;
import java.util.List;

/** Application service for the Notification aggregate. */
public class NotificationService {

    /** Create a new Notification from a partial input. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Notification by id; returns null if not found. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Notifications, capped at the supplied limit. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Notification by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

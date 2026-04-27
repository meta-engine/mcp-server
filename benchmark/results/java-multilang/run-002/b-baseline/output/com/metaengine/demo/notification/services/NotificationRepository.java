package com.metaengine.demo.notification.services;

import java.util.List;
import com.metaengine.demo.notification.aggregates.Notification;

/** NotificationRepository in the notification domain. */
public class NotificationRepository {
    /** Create a new Notification. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Notification by id. Returns null if not found. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Notifications up to limit. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Notification by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

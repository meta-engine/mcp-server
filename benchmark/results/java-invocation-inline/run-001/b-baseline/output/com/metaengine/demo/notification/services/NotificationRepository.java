package com.metaengine.demo.notification.services;

import com.metaengine.demo.notification.aggregates.Notification;
import java.util.List;

/** Persistence gateway for notifications. */
public class NotificationRepository {
    /** Persist a new notification from the provided partial input. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load a notification by id. Returns null when not found. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} notifications. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove a notification by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

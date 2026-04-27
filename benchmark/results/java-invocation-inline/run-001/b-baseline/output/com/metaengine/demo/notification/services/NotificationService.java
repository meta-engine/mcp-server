package com.metaengine.demo.notification.services;

import com.metaengine.demo.notification.aggregates.Notification;
import java.util.List;

/** Application service exposing notification operations. */
public class NotificationService {
    /** Create a notification from the provided partial input. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a notification by id. Returns null when not found. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} notifications. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a notification by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

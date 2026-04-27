package com.metaengine.demo.notification.services;

import com.metaengine.demo.notification.aggregates.Notification;
import java.util.List;

/** NotificationRepository service for the notification domain. */
public class NotificationRepository {

    /** Create a new Notification. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Notification by id. May return null. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List notifications up to the given limit. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Notification by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

package com.metaengine.demo.notification.services;

import com.metaengine.demo.notification.aggregates.Notification;
import java.util.List;

/** NotificationRepository for the notification domain. */
public class NotificationRepository {

    /** Persist a new Notification. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load a Notification by id; may return null. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List notifications up to the given limit. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a notification by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

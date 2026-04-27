package com.metaengine.demo.notification.services;

import java.util.List;

import com.metaengine.demo.notification.aggregates.Notification;

/** NotificationService for the notification domain. */
public class NotificationService {

    /** Creates a new Notification from the partial input. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Finds a Notification by id. May return null. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Lists Notifications up to the given limit. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Deletes the Notification with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

package com.metaengine.demo.notification.services;

import com.metaengine.demo.notification.aggregates.Notification;
import java.util.List;
import java.util.Optional;

/** NotificationRepository persistence service for the notification domain. */
public class NotificationRepository {
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    public Optional<Notification> findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

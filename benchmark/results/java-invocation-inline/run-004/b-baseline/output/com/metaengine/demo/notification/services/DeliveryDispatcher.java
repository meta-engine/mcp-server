package com.metaengine.demo.notification.services;

import java.util.List;
import com.metaengine.demo.notification.aggregates.Notification;

/** DeliveryDispatcher domain service. */
public class DeliveryDispatcher {
    /** Dispatch a Notification for delivery. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Notification by id; returns null if not found. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to limit Notifications. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Cancel a queued Notification by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

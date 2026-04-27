package com.metaengine.demo.notification.services;

import java.util.List;

import com.metaengine.demo.notification.aggregates.Notification;

/** DeliveryDispatcher domain service. */
public class DeliveryDispatcher {

    /** Dispatch a Notification for delivery. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Notification by id (may return null). */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List notifications up to limit. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Notification by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

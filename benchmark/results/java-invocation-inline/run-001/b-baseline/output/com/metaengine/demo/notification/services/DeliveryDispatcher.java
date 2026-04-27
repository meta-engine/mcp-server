package com.metaengine.demo.notification.services;

import com.metaengine.demo.notification.aggregates.Notification;
import java.util.List;

/** Domain service that dispatches notifications to the relevant channels. */
public class DeliveryDispatcher {
    /** Dispatch a notification from the provided partial input. */
    public Notification create(Notification input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Look up a dispatched notification by id. Returns null when not found. */
    public Notification findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} dispatched notifications. */
    public List<Notification> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Cancel dispatch for the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

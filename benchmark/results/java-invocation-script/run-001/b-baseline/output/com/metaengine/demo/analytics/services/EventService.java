package com.metaengine.demo.analytics.services;

import com.metaengine.demo.analytics.aggregates.Event;
import java.util.List;

/** EventService for the analytics domain. */
public class EventService {

    /** Create a new Event. */
    public Event create(Event input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Event by id; may return null. */
    public Event findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List events up to the given limit. */
    public List<Event> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an event by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

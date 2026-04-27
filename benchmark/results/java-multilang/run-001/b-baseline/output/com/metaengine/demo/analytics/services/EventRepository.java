package com.metaengine.demo.analytics.services;

import java.util.List;

import com.metaengine.demo.analytics.aggregates.Event;

/** EventRepository for the analytics domain. */
public class EventRepository {

    /** Persists a new Event from the partial input. */
    public Event create(Event input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Finds an Event by id. May return null. */
    public Event findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Lists Events up to the given limit. */
    public List<Event> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Deletes the Event with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

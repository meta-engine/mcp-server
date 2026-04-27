package com.metaengine.demo.identity.services;

import com.metaengine.demo.identity.aggregates.User;
import java.util.List;

/** Authentication service for the User aggregate. */
public class AuthService {

    /** Create a new User credential from a partial input. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a User by id; returns null if not found. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Users, capped at the supplied limit. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a User credential by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

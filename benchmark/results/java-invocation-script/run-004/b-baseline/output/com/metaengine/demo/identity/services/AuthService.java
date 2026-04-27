package com.metaengine.demo.identity.services;

import com.metaengine.demo.identity.aggregates.User;
import java.util.List;

/** AuthService domain service in the identity domain. */
public class AuthService {
    /** Authenticate and create a User from a partial input. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a User by id, or null if not found. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Users up to limit. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a User by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

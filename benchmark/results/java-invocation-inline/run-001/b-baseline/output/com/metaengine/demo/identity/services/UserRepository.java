package com.metaengine.demo.identity.services;

import com.metaengine.demo.identity.aggregates.User;
import java.util.List;

/** Persistence gateway for users. */
public class UserRepository {
    /** Persist a new user from the provided partial input. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load a user by id. Returns null when not found. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} users. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove a user by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

package com.metaengine.demo.identity.services;

import com.metaengine.demo.identity.aggregates.User;
import java.util.List;

/** Application service exposing user operations. */
public class UserService {
    /** Create a user from the provided partial input. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a user by id. Returns null when not found. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} users. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a user by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

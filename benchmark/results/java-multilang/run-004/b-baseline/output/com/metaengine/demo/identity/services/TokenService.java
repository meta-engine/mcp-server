package com.metaengine.demo.identity.services;

import java.util.List;

import com.metaengine.demo.identity.aggregates.User;

/** TokenService domain service. */
public class TokenService {

    /** Issue a token for a User. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a User by id (may return null). */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List users up to limit. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a User by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

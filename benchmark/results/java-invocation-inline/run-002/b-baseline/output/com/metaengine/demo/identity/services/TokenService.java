package com.metaengine.demo.identity.services;

import java.util.List;

import com.metaengine.demo.identity.aggregates.User;

/** TokenService for the identity domain. */
public class TokenService {

    /** Create a new User from partial input. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a User by id. Returns null if not found. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Users up to the given limit. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete the User with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

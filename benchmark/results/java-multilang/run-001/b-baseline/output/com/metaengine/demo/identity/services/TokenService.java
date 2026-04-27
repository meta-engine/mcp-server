package com.metaengine.demo.identity.services;

import java.util.List;

import com.metaengine.demo.identity.aggregates.User;

/** TokenService for the identity domain. */
public class TokenService {

    /** Creates a new User from the partial input. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Finds a User by id. May return null. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Lists Users up to the given limit. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Deletes the User with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

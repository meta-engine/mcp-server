package com.metaengine.demo.identity.services;

import com.metaengine.demo.identity.aggregates.User;
import java.util.List;

/** TokenService for the identity domain. */
public class TokenService {

    /** Issue a token for a User. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a User by id; may return null. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List users up to the given limit. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a user by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}

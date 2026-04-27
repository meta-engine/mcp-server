package com.metaengine.demo.identity.services;

import com.metaengine.demo.identity.aggregates.User;
import java.util.List;

/** UserService for the identity domain. */
public class UserService {

    /** Create a new User. */
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

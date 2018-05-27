package org.BootWeb.Dao;

import org.BootWeb.Entity.User;
import org.springframework.data.repository.CrudRepository;

public interface UserMapper extends CrudRepository<User,Integer> {
	
}

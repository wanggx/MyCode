//
//  FavorLogo+CoreDataProperties.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/19.
//  Copyright © 2015年 sapphire. All rights reserved.
//
//  Choose "Create NSManagedObject Subclass…" from the Core Data editor menu
//  to delete and recreate this implementation file for your updated model.
//

import Foundation
import CoreData


extension FavorLogo {

    @NSManaged var uid: String?
    @NSManaged var date: String?
    @NSManaged var image: String?

}

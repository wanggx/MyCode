//
//  Market.swift
//  SapphireReleaseAutoLayOut
//
//  Created by gxwang on 15/7/21.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import CoreData

@objc(Market)
class Market: NSManagedObject {

    @NSManaged var brandid:NSNumber
    @NSManaged var brand: String
    @NSManaged var cid: String
    @NSManaged var price: NSNumber
    @NSManaged var sales: NSNumber
    @NSManaged var color: String
    @NSManaged var size: String
    @NSManaged var defaultImage: String
    @NSManaged var image: String
    @NSManaged var title: String
    @NSManaged var descript: String
    @NSManaged var type:NSNumber
    @NSManaged var favor:String

}

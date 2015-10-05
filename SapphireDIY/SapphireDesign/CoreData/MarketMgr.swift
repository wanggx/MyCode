//
//  MarketMgr.swift
//  SapphireReleaseAutoLayOut
//
//  Created by gxwang on 15/7/7.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit
import CoreData
import Alamofire
import SwiftyJSON

private let STR_MARKET_ENTITY_NAME = "Market"


enum eDataType {
    case TYPE_TSHIRT
    case TYPE_RECOMMEND
    case TYPE_BRAND(String)
}


class MarketMgr : CoreDataClothes
{
    var type:eDataType?
    
    init (_type:eDataType?) {
        type = _type
    }
    
    private func getPredict()->NSPredicate? {
        if type == nil {
            return nil
        }
        var format:String = ""
        switch type! {
        case .TYPE_TSHIRT:
            format = "type == '0'"
        case .TYPE_BRAND(let str):
            format = "brand contains '\(str)'"
        default:
            return nil
        }
        log.info("format is \(format)")
        return NSPredicate(format: format, argumentArray: nil)
    }
    
    override func getFetchRequest() -> NSFetchRequest? {
        let fetchRequest = NSFetchRequest(entityName:STR_MARKET_ENTITY_NAME )
        fetchRequest.sortDescriptors = []
        fetchRequest.predicate = getPredict()
        return fetchRequest
    }
    
    override func getEntityName() -> String {
        return STR_MARKET_ENTITY_NAME
    }

    private func Convert(fromMarket:Market,inout toMarketInfo:MarketItemInfo) {
        toMarketInfo.cid = fromMarket.cid
        toMarketInfo.numSales = fromMarket.sales.longValue
        toMarketInfo.netImage = fromMarket.defaultImage
        toMarketInfo.cid = fromMarket.cid
        toMarketInfo.numSales = fromMarket.sales.longValue
        toMarketInfo.price = fromMarket.price.doubleValue
        var clothesColor:SaClothesColor = SaClothesColor()
        clothesColor.color = fromMarket.color
        toMarketInfo.clothesColor = clothesColor
        toMarketInfo.brandStr = fromMarket.brand
        toMarketInfo.title = fromMarket.title
        toMarketInfo.description = fromMarket.descript
        log.info("cid is \(toMarketInfo.cid)")
        log.info("netImage is \(toMarketInfo.netImage)")
    }
    
    private func Convert(fromJSON:JSON,inout toMarketInfo:Market) {
        toMarketInfo.cid = fromJSON["costume_id"].stringValue
        toMarketInfo.defaultImage = fromJSON["image_url"].stringValue
        toMarketInfo.image = fromJSON["image_url"].stringValue
        toMarketInfo.price = fromJSON["price"].numberValue
        toMarketInfo.sales = fromJSON["sales_volume"].numberValue
        toMarketInfo.price = fromJSON["price"].numberValue
        toMarketInfo.color = fromJSON["color"].stringValue
        toMarketInfo.descript = fromJSON["costume_describe"].stringValue
        toMarketInfo.brand = fromJSON["brand_name"].stringValue
        toMarketInfo.title = fromJSON["title"].stringValue
        log.info("cid is \(toMarketInfo.cid)")
    }
    
    override func processCoreDataItem(item: AnyObject) -> AnyObject {
        var marketItem:MarketItemInfo = MarketItemInfo()
        Convert(item as! Market, toMarketInfo: &marketItem)
        return marketItem
    }
    
    override func addJSONData(json: JSON) -> Bool {
        log.info("\(json)")
        var cid = json["costume_id"].stringValue
        log.info("cid is \(cid)")
        if IsExist(["cid":json["costume_id"].stringValue]) == true {
            return false
        }
        
        let ent = NSEntityDescription.entityForName(STR_MARKET_ENTITY_NAME, inManagedObjectContext: GlobalFunc.CoreContext)
        var nItem = Market(entity: ent!, insertIntoManagedObjectContext: GlobalFunc.CoreContext)
        
        Convert(json, toMarketInfo: &nItem)
        GlobalFunc.CoreContext.save(nil)
        return true
    }
    
    override func getNetRequest() -> Request? {
        if type==nil {
            return nil
        }
        var url:NSURL?
        switch type! {
        case .TYPE_TSHIRT:
            url = GlobalUrl.URL_GET_TSHIRT_DATA
            log.info("fetchUrl is \(url)")
        case .TYPE_RECOMMEND:
            url = GlobalUrl.URL_GET_RECOMMAND_DATA
        case .TYPE_BRAND(let str):
            return Alamofire.request(.GET, GlobalUrl.URL_GET_BRAND_DATA, parameters: ["myBrandName":str])
        default:
            return nil
        }
        if url == nil {
            return nil
        }
        return Alamofire.request(.GET, url!)
    }
}
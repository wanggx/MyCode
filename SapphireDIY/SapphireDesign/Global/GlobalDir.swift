//
//  SaDirMgr.swift
//  SapphireRelease
//
//  Created by 冯 波 on 15/4/2.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation

let PATH_DOCUMENT         = "Documents"
let PATH_IMAGECACHE       = "imageCache"
let PATH_HEADVIEWCACHE    = "HeadView"
let PATH_ADVERTISECACHE   = "Ads"
let PATH_CACHEDATAINPLIST = "data.plist"
let PATH_BRAND_TOTAL      = "brandtotal"

class GlobalDir
{
    class var documentsDirectory: NSURL {
        let urls = NSFileManager.defaultManager().URLsForDirectory(.DocumentDirectory, inDomains: .UserDomainMask)
        return urls[urls.endIndex-1] 
    }
    
    class var cacheDirectory: NSURL {
        let urls = NSFileManager.defaultManager().URLsForDirectory(.CachesDirectory, inDomains: .UserDomainMask)
        return urls[urls.endIndex-1] 
    }
    
    class var cacheLogDirectory:NSURL {
        return GlobalDir.cacheDirectory.URLByAppendingPathComponent(SALOG)
    }
    
    class func cacheDataInPlist()->NSURL
    {
        return GlobalDir.cacheDirectory.URLByAppendingPathComponent(PATH_CACHEDATAINPLIST)
    }
    
    class var userHeadViewDirectory:String {
        let Url = NSHomeDirectory().stringByAppendingString(PATH_DOCUMENT).stringByAppendingString(PATH_IMAGECACHE).stringByAppendingString(PATH_HEADVIEWCACHE)
        //log.info(Url)
        if createDirectory(Url) == true {
            return Url
        }
        return ""
    }
    
    class var appAdsDirectory:String {
        let Url = NSHomeDirectory().stringByAppendingString(PATH_DOCUMENT).stringByAppendingString(PATH_IMAGECACHE).stringByAppendingString(PATH_ADVERTISECACHE)
        //log.info(Url)
        if createDirectory(Url) == true {
            return Url
        }
        return ""
    }
    
    class var imageCacheUrl:NSURL {
        let cacheUrl = documentsDirectory.URLByAppendingPathComponent(PATH_IMAGECACHE)
        createDirectoryByUrl(cacheUrl)
        return cacheUrl
    }
    
    class func userImageCacheURL(userName:String)->NSURL {
        let userHeadViewDirectory = documentsDirectory.URLByAppendingPathComponent(PATH_IMAGECACHE).URLByAppendingPathComponent(PATH_HEADVIEWCACHE)
        
        let userHeadViewPath = userHeadViewDirectory.URLByAppendingPathComponent(userName + ".png")
        print(userHeadViewPath)
        return userHeadViewPath
    }
    
    class func getUserImageCache(userName:String) -> String
    {
        let userHeadViewDirectory = GlobalDir.userHeadViewDirectory
        let userHeadViewPath = userHeadViewDirectory + "/" + userName + ".png"
        return userHeadViewPath
    }
    
    class func getClothesImageLocalDir(cid:String)->String
    {
        let dir = NSHomeDirectory().stringByAppendingString(PATH_DOCUMENT).stringByAppendingString(PATH_IMAGECACHE).stringByAppendingString(cid)
        //log.info(dir)
        if createDirectory(dir) == true
        {
            return dir+"/"
        }
        return ""
    }
    
    class func getClothesImageByIdAndColor(cid:String,color:String)->String {
        let dir = getClothesImageLocalDir(cid).stringByAppendingString(color)
        if createDirectory(dir) == true {
            return dir+"/"
        }
        return ""
    }
    
    class func getClothesDetailImageById(cid:String)->String {
        let dir = getClothesImageLocalDir(cid).stringByAppendingString("main")
        if createDirectory(dir) == true {
            return dir+"/"
        }
        return ""
    }
    
    class func getClothesImageCacheDir(cid:String)->NSURL
    {
        var clothesDir:String = GlobalDir.getClothesImageLocalDir(cid)
        let clothesImageCacheDirectory = documentsDirectory.URLByAppendingPathComponent(PATH_IMAGECACHE).URLByAppendingPathComponent(cid)
        return clothesImageCacheDirectory
    }
    
    class func getAdvDirString()->String
    {
        let dir = NSHomeDirectory().stringByAppendingString(PATH_DOCUMENT).stringByAppendingString(PATH_IMAGECACHE).stringByAppendingString(PATH_ADVERTISECACHE)
        //log.info(dir)
        if createDirectory(dir) == true
        {
            return dir+"/"
        }
        return ""
    }
    
    class func getBrandDirString() -> String
    {
        let dir = NSHomeDirectory().stringByAppendingString(PATH_DOCUMENT).stringByAppendingString(PATH_IMAGECACHE).stringByAppendingString(PATH_BRAND_TOTAL)
        if createDirectory(dir) == true
        {
            return dir+"/"
        }
        return ""
    }
    
    class func getAdvDirUrl()->NSURL
    {
        var clothesDir:String = GlobalDir.getAdvDirString()
        let clothesImageCacheDirectory = documentsDirectory.URLByAppendingPathComponent(PATH_IMAGECACHE).URLByAppendingPathComponent(PATH_ADVERTISECACHE)
        return clothesImageCacheDirectory
    }
    
    class func createDirectory(dirPath:String) -> Bool
    {
        let tmpDirPath = dirPath
        let fileManager = NSFileManager.defaultManager()
        if(!fileManager.fileExistsAtPath(tmpDirPath)) {
            var flag: Bool
            do {
                try fileManager.createDirectoryAtPath(tmpDirPath, withIntermediateDirectories: true, attributes: nil)
                flag = true
            } catch _ {
                flag = false
            }
            return flag
        }
        return true
    }
    
    class func removeStringDir(dir:String)->Bool {
        do {
            try NSFileManager.defaultManager().removeItemAtPath(dir)
            return true
        } catch _ {
            return false
        }
    }
    
    class func removeUrlDir(dir:NSURL)->Bool {
        do {
            try NSFileManager.defaultManager().removeItemAtURL(dir)
            return true
        } catch _ {
            return false
        }
    }
    
    //创建目录，通过URL的形式
    class func createDirectoryByUrl(urlPath:NSURL) ->Bool {
        
        let fileManager = NSFileManager.defaultManager()
        do {
            try fileManager.createDirectoryAtURL(urlPath, withIntermediateDirectories: true, attributes: nil)
            return true
        } catch _ {
            return false
        }
    }
    
    //删除文件
    class func removeFileByUrl(urlPath:NSURL)->Bool {
        let fileManager = NSFileManager.defaultManager()
        do {
            try fileManager.removeItemAtURL(urlPath)
            return true
        } catch _ {
            return false
        }
    }
    
    //判断在某个文件是否存在
    class func fileExistAtPath(filePath:String)->Bool {
        let fileManager = NSFileManager.defaultManager()
        return fileManager.fileExistsAtPath(filePath)
    }
    
    class func isPathExist(path:String)->Bool
    {
        let fileManager = NSFileManager.defaultManager()
        if(!fileManager.fileExistsAtPath(path))
        {
            return false
        }
        return true
    }

}
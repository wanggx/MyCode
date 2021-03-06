//
//  GlobalCode.swift
//  SapphireDesign
//
//  Created by gxwang on 15/9/1.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation

let ERROR_CODE_NO_ERROR = 0
let ERROR_CODE_ERROR_PWD = 1
let ERROR_CODE_ERROR_NETWORK = 2
let ERROR_CODE_REFRESH_ERROR = 3



func processErrorCode(code:Int) {
    
    switch code {
    case ERROR_CODE_ERROR_PWD:
        SwiftNotice.showNoticeWithText(.error, text: "密码错误", autoClear: true)
    case ERROR_CODE_ERROR_NETWORK:
        SwiftNotice.showNoticeWithText(.error, text: "网络错误", autoClear: true)
    default:
        return
    }
}

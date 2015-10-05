//
//  LabelFontNameFactory.swift
//  SapphireDesign
//
//  Created by 波 冯 on 15/9/15.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//



class LabelFontNameFactory {
    
    var fontNames = ["Chalkduster","TimesNewRomanPSMT","AmericanTypewriter-CondensedLight","Courier","Didot-Bold","AmericanTypewriter-CondensedBold","Arial-ItalicMT","BanglaSangamMN","Baskerville-BoldItalic","BodoniSvtyTwoOSITCTT-BookIt","BradleyHandITCTT-Bold","Cochin-BoldItalic","Courier-BoldOblique","Futura-CondensedMedium","Helvetica","MarkerFelt-Wide","Noteworthy-Light","Palatino-Italic","Papyrus-Condensed","SnellRoundhand-Bold","Zapfino"]
    
    func getFontCount() -> Int
    {
        return fontNames.count
    }
    
    func getFontNameByIndex(index:Int) -> String
    {
        return fontNames[index]
    }
    
    func getFontIndexByName(name:String) -> Int
    {
        for(var i:Int = 0; i < fontNames.count; i++)
        {
            if(fontNames[i] == name)
            {
                return i
            }
        }
        return 0
    }
    
}

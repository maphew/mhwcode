import ConversionUtils, time

ConversionUtils.gp.Overwriteoutput = 1

#Define message constants so they may be translated easily
msgErrorInvalidOutPath = "Output path does not exist"
msgSuccess = "successfully converted to "
msgFailed = "Failed to convert "

# Argument 1 is the list of feature classes to be converted
inFeatureClasses = ConversionUtils.gp.GetParameterAsText(0)

# The list is split by semicolons ";"
inFeatureClasses = ConversionUtils.SplitMultiInputs(inFeatureClasses)

# The output workspace where the shapefiles are created
outWorkspace = ConversionUtils.gp.GetParameterAsText(1)

# Set the destination workspace parameter (which is the same value as the output workspace)
# the purpose of this parameter is to allow connectivity in Model Builder.
ConversionUtils.gp.SetParameterAsText(2,outWorkspace)

# Set the progressor
ConversionUtils.gp.SetProgressor("step", "Converting multiple feature classes ...", 0, len(inFeatureClasses))

# Loop through the list of input feature classes and convert/copy each to the output geodatabase or folder
for inFeatureClass in inFeatureClasses:
    try:
        # Set the progressor label
        ConversionUtils.gp.SetProgressorLabel("Converting " + inFeatureClass)

        # Generate a valid output output name
        outFeatureClass = ConversionUtils.GenerateOutputName(inFeatureClass, outWorkspace)

        # Copy/Convert the inFeatureClasses to the outFeatureClasses
        ConversionUtils.CopyFeatures(inFeatureClass, outFeatureClass)

        # If the Copy/Convert was successfull add a message stating this
        ConversionUtils.gp.AddMessage("%s %s %s" % (inFeatureClass, msgSuccess, outFeatureClass))

    except Exception, ErrorDesc:
        # Except block for the loop. If the tool fails to convert one of the feature classes, it will come into this block
        #  and add warnings to the messages, then proceed to attempt to convert the next input feature class.
        msgWarning = msgFailed + "%s" % inFeatureClass
        msgStr = ConversionUtils.gp.GetMessages(2)
        ConversionUtils.gp.AddWarning(ConversionUtils.ExceptionMessages(msgWarning, msgStr, ErrorDesc))

    ConversionUtils.gp.SetProgressorPosition()

time.sleep(0.5) 

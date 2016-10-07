
                  
PRICE_FEED = '_POST_PRODUCT_PRICING_DATA_'
PRODUCT_FEED = '_POST_PRODUCT_DATA_'
INVENTORY_FEED = '_POST_INVENTORY_AVAILABILITY_DATA_'

class ProcessingStatus:
    #I need to generate and send this feed to Amazon NOTE: This is an internal, not an amazon Status
    REQUESTED = 'REQUESTED'
    #The request is being processed, but is waiting for external information before it can complete.
    WAITING_REPLY = '_AWAITING_ASYNCHRONOUS_REPLY_'
    #The request has been aborted due to a fatal error.
    CANCELLED = '_CANCELLED_'
    #The request has been processed. You can call the GetFeedSubmissionResult operation to receive 
    #    a processing report that describes which records in the feed were successful and which records 
    #    generated errors.
    DONE = '_DONE_'
    #The request is being processed.
    IN_PROGRESS = '_IN_PROGRESS_'
    #The request is being processed, but the system has determined that there is a potential error with 
    #    the feed (for example, the request will remove all inventory from a seller's account.) An Amazon 
    #    seller support associate will contact the seller to confirm whether the feed should be processed.
    IN_SAFETY_NET = '_IN_SAFETY_NET_'
    #The request has been received, but has not yet started processing.
    SUBMITTED = '_SUBMITTED_'
    #The request is pending.
    PENDING = '_UNCONFIRMED_'
    FINAL_STATES = [CANCELLED, DONE, IN_SAFETY_NET]
    ERROR_STATES = [WAITING_REPLY, CANCELLED, IN_SAFETY_NET]

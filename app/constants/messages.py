class AllMessages:
    HTTP_MESSAGES = {
        200: "Success",
        201: "Created Successfully",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error"
    }
    
class ErrorMessages:
    SORT_COLUMN_NOT_IN_SELECT = "Sort column is not in select statement"
from fastapi import APIRouter, Request

from .views import predict_one, prepare_data,prepare_data_a, predict_csv  # Importez vos fonctions de vues ici

api_router = APIRouter()

@api_router.get("/status")
async def get_status():
    return {"message": "OK"}



@api_router.post("/predict_One")
async def predict_One(request: Request):
    # Get JSON data
    data = await request.json()
    #print(data)
    # Example processing of the data:
    df = prepare_data_a(data)

    result = predict_one(df)
    
    # For now, let's return the received data for debugging:
    return {"result" : result}

@api_router.post("/predict_csv")
async def predict_Csv(request: Request):
    # Get JSON data
    data = await request.json()
    #print(data)
    df = prepare_data(data)
    if df is None:
      return {'Error': '+300 CSV'}

    result = predict_csv(df)
    
    # For now, let's return the received data for debugging:
    return {"data" : data, "result" : result}

@api_router.post("/predict_test")
async def predict_test(request: Request):
    # Get JSON data
    data = await request.json()
    #print(data)
    # Example processing of the data:
    df = prepare_data_a(data)

    result = predict_one(df)
    
    # For now, let's return the received data for debugging:
    return {"result" : result}

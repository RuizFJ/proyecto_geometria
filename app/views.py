import logging
from django.http import JsonResponse
from sympy import symbols, diff, integrate, sympify, SympifyError, lambdify, latex
import json
from django.shortcuts import render
import re
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

logger = logging.getLogger('appgeometria')

def home(request):
    return render(request, 'home.html')

def calculator(request):
    return render(request, 'calculator.html')

def calculate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression')
            operation = data.get('operation')
            limite_inferior = data.get('limite_inferior', None)
            limite_superior = data.get('limite_superior', None)
            dimension = data.get('dimension', '2D')  # Nuevo: obtener la dimensión (2D o 3D)
            expression = re.sub(r"(?<=\d)x", "*x", expression)
            
            # Reemplazar expresiones para que sympy las reconozca
            expression = (expression.replace('f(x)=', '')
                        .replace('^', '**')
                        .replace('√', 'sqrt')
                        .replace('π', 'pi')
                        #.replace('e', 'E')  # Añadido para constante e
                        .replace('sin', 'sin')  # Función trigonométrica
                        .replace('cos', 'cos')  # Función trigonométrica
                        .replace('tan', 'tan')  # Función trigonométrica
                        .replace('csc', 'csc')  # Función trigonométrica
                        .replace('sec', 'sec')  # Función trigonométrica
                        .replace('cot', 'cot')  # Función trigonométrica
                        .replace('sinh', 'sinh')  # Función hiperbólica
                        .replace('cosh', 'cosh')  # Función hiperbólica
                        .replace('tanh', 'tanh')  # Función hiperbólica
                        .replace('csch', 'csch')  # Función hiperbólica
                        .replace('sech', 'sech')  # Función hiperbólica
                        .replace('coth', 'coth')  # Función hiperbólica
                        .replace('log', 'log')  # Logaritmo
                        .replace('ln', 'log')  # Logaritmo natural (ln)
                        .replace('exp', 'exp')  # Función exponencial
                        .replace('asin', 'asin')  # Función trigonométrica inversa
                        .replace('acos', 'acos')  # Función trigonométrica inversa
                        .replace('atan', 'atan'))  # Función trigonométrica inversa

            if dimension == '3D':
                x, y = symbols('x y')  # agregar símbolo 'y' para 3D
            else:
                x = symbols('x')

            if operation == 'Derivar':
                if dimension == '3D': # derivar con respecto a 'x' y 'y' en 3D
                    result_x = str(diff(expression, x)) # derivada parcial con respecto a 'x'
                    result_y = str(diff(expression, y))
                    result = f'df/dx={result_x}, df/dy={result_y}'
                else:
                    result = str(diff(expression, x)) # derivada con respecto a 'x' en 2D
                resultFunc = 'f(x)=' + result.replace('**', '^').replace('sqrt', '√').replace('pi', 'π') 

            elif operation == 'Integrar':
                if limite_inferior is not None and limite_superior is not None: # integrar con límites
                    result = str(integrate(expression, (x, float(limite_inferior), float(limite_superior)))) 
                    resultFunc = f'f(x) = ∫({expression})dx from {limite_inferior} to {limite_superior} = ' + result.replace('**', '^').replace('sqrt', '√').replace('pi', 'π')
                else:
                    antiderivative = integrate(expression, x)
                    result = str(antiderivative)
                    resultFunc = 'f(x) = ∫(' + expression + ')dx = ' + result.replace('**', '^').replace('sqrt', '√').replace('pi', 'π')

                    # Agregar constante solo si es una integral indefinida
                    if 'C' not in result:
                        resultFunc += ' + C'

                    
            else:
                return JsonResponse({'error': 'Invalid operation'}, status=400) 

            if dimension == '3D':  # generación de gráfico 3D
                expr = sympify(expression)
                
                x_vals = np.linspace(-10, 10, 100)
                y_vals = np.linspace(-10, 10, 100)
                x_vals, y_vals = np.meshgrid(x_vals, y_vals)  # generar malla de valores de 'x' y 'y'
                f = lambdify((x, y), expr, modules=["numpy"])
                z_vals = f(x_vals, y_vals)

                fig = go.Figure(data=[go.Surface(z=z_vals, x=x_vals, y=y_vals)]) # crear gráfico 3D
                fig.update_layout(title=resultFunc, autosize=True, margin=dict(l=65, r=50, b=65, t=90))

                graph_div = pio.to_html(fig, full_html=False) # convertir gráfico a HTML
            else:
                expr = sympify(expression)
                x_vals = np.linspace(-10, 10, 400)
                f = lambdify(x, expr, modules=["numpy"])
                y_vals = f(x_vals)
                
                fig = go.Figure(data=[go.Scatter(x=x_vals, y=y_vals)]) # crear gráfico 2D
                fig.update_layout(title=resultFunc, xaxis_title='x', yaxis_title='f(x)')

                graph_div = pio.to_html(fig, full_html=False) # convertir gráfico a HTML

            return JsonResponse(  # devolver resultado y gráfico
                {
                    'result': result,
                    'resultFunc': resultFunc,
                    'original': expression,
                    'graph': graph_div
                })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except SympifyError:
            return JsonResponse({'error': 'Invalid mathematical expression'}, status=400)
        except Exception as e:
            logger.error("An error occurred: %s", str(e))
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=405)

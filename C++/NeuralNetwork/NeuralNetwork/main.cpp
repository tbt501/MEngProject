/****************************************************************************************************************/
/*                                                                                                              */
/*   OpenNN: Open Neural Networks Library                                                                       */
/*   www.intelnics.com/opennn                                                                                   */
/*                                                                                                              */
/*   S I M P L E   P A T T E R N   R E C O G N I T I O N   A P P L I C A T I O N                                */
/*                                                                                                              */
/*   Roberto Lopez                                                                                              */
/*   Intelnics - The artificial intelligence company                                                            */
/*   robertolopez@intelnics.com                                                                                 */
/*                                                                                                              */
/****************************************************************************************************************/

// This is a pattern recognition problem.

// System includes

#include <iostream>
#include <sstream>
#include <time.h>
#include <stdexcept>

// OpenNN includes

#include "/Users/Angelo555uk/Desktop/GitR/MEngProject/C++/NeuralNetwork/NeuralNetwork/OpenNN/opennn/opennn.h"

using namespace OpenNN;

int main(void)
{
    try
    {
        std::cout << "OpenNN. Simple Pattern Recognition Application." << std::endl;
        
        srand( (unsigned)time( NULL ) );
        
        // Data set object
        
        DataSet data_set;
        data_set.set_data_file_name("/Users/Angelo555uk/Desktop/GitR/MEngProject/C++/NeuralNetwork/NeuralNetwork/OpenNN/examples/simple_pattern_recognition/data/simplepatternrecognition.dat");
        
        data_set.load_data();
        
        Variables* variables_pointer = data_set.get_variables_pointer();
        
        variables_pointer->set_name(0, "x1");
        variables_pointer->set_name(1, "x2");
        variables_pointer->set_name(2, "y");
        
        Instances* instances_pointer = data_set.get_instances_pointer();
        
        instances_pointer->set_training();
        
        Matrix<std::string> inputs_information = variables_pointer->arrange_inputs_information();
        Matrix<std::string> targets_information = variables_pointer->arrange_targets_information();
        
        const Vector< Statistics<double> > inputs_statistics = data_set.scale_inputs_minimum_maximum();
        
        
        return(0);
    }
    catch(std::exception& e)
    {
        std::cerr << e.what() << std::endl;
        
        return(1);
    }
}


// OpenNN: Open Neural Networks Library.
// Copyright (C) 2005-2014 Roberto Lopez
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.

// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
